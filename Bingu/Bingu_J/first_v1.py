from Bingu.Bingu_C.get_lineprogress import Get_Lineprogress
from Bingu.Bingu_C import caculate
from flask.json import jsonify
from Bingu.Bingu_C.canny import Edge


class KneeJson:
    def __init__(self):
        edge = Edge('test11.png')
        edge.operation_image()

    @classmethod
    def patella_angle(cls):
        """
        髌股关节面角：即髌骨内外关节面所成之角，正常约130°，大致与股沟角相当。
        髌骨的夹角
        :return:
        """
        pass

    @classmethod
    def femur_angle(cls):
        """
        股沟角：由股骨内、外侧髁顶点至股骨滑车底连线所成的髁间角，正常为138°〜142°。在髌骨半脱位可增大，说明股骨下端发育不良可导致髌骨不稳定
        股骨的夹角。
        :return:
        """
        pass

    @classmethod
    def fit_angle(cls):
        """
        适应角：在股沟角作平分线，其与髌骨最低点和沟底连线之间的夹角即适应角，正常此角偏向内髁侧，为-6°〜-9°，如偏向外髁侧，则为正值，适应角的大小提示髌骨的稳定情况。有髌骨不稳定者，其适应角均增大。
        :return:
        """
        pass

    @classmethod
    def double_center_angle(cls):
        """
        双中心角：髌骨内外缘连线中点和沟底连线与股沟角平分线所成夹角称为双中心角，测量结果显示其与适应角数值近似
        :return:
        """
        pass

    @classmethod
    def outside_patella_angle(cls):
        """
        外侧髌股角：为股骨内、外侧髁连线与髌骨外侧关节面所成之角，正常约为15°。在髌骨半脱位，两线多呈平行，甚至向内成角
        :return:
        """
        pass

    @classmethod
    def patella_slant_angle(cls):
        """
        髌倾斜角：为髌骨内外缘连线及股骨内、外侧髁连线相交之角，正常约为11°，在髌骨半脱位时可增大。
        :return:
        """
        pass

    @classmethod
    def patella_index(cls):
        """
        髌股指数：内侧髌股关节间隙最短距离与外侧髌股关节最短距离之比。正常髌骨指数＜1.6，髌股关节炎因外侧超负荷，致软骨磨损变薄，髌股指数增大>1.6，可表明髌骨倾斜或半脱位
        :return:
        """
        pass

    @classmethod
    def palella_proportion(cls):
        """
        髌骨关节面比例：髌骨外侧关节面与内侧关节面长度之比，正常外侧关节面较长，比率为1.1~1.2。此比率可反映关节面的形态。
        :return:
        """
        pass

    def get_point_from_image(self):
        """
        从图片中，获取关键点
        :return:
        """
        pass

    def create_json(self):
        """
        最终返回json格式结果的函数
        :return:
        """
        return ''


if __name__ == '__main__':
    # kneejson = KneeJson()
    pass
